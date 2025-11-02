import logging
from typing import List, Optional, Tuple, Union
from uuid import uuid4

from aiohttp.web import HTTPNoContent, HTTPNotFound
from aiohttp_pydantic.oas.typing import r200, r201, r204

from prozorro_cdb.api.context import (
    get_request_logging_context,
    get_view_url,
    url_to_absolute,
)
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.errors import JsonHTTPNotFound
from prozorro_cdb.api.handlers.base import BaseView
from prozorro_cdb.api.handlers.schema.common import DataModel
from prozorro_cdb.api.middlewares import json_response
from prozorro_cdb.api.serializers.document import DocumentSerializer
from prozorro_cdb.api.storage import download_file
from prozorro_cdb.violation_report.database.helpers import (
    get_violation_report_or_404,
    update_violation_report,
)
from prozorro_cdb.violation_report.database.schema.violation_report import (
    DecisionDBModel,
    DraftActiveObjectStatus,
    ViolationReportDBModel,
)
from prozorro_cdb.violation_report.handlers.schema.decision import (
    DecisionActivateRequestData,
    DecisionPatchRequestData,
    DecisionPostRequestData,
)
from prozorro_cdb.violation_report.handlers.schema.document import (
    PatchDocument,
    PostDocument,
)
from prozorro_cdb.violation_report.serializers.decision import (
    ViolationReportDecisionSerializer,
)
from prozorro_cdb.violation_report.state.decision import ViolationReportDecisionState

logger = logging.getLogger(__name__)


class ViolationReportDecisionListView(BaseView):
    view_name = "violation_report_decision_list"

    async def get(self, violation_report_id: str, /) -> r200[DataModel[list[DecisionDBModel]]]:
        """
        Tags: ViolationReports.decisions
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        return {
            "data": [
                ViolationReportDecisionSerializer(d).data
                for d in violation_report.decisions
                if d.status != DraftActiveObjectStatus.draft
            ]
        }

    async def post(
        self, violation_report_id: str, /, body: DataModel[DecisionPostRequestData]
    ) -> r201[DataModel[DecisionDBModel]]:
        """
        Tags: ViolationReports.decisions
        """
        violation_report = await get_violation_report_or_404(violation_report_id)

        # create state and validate input
        ViolationReportDecisionState.validate_create(violation_report=violation_report)

        # create obj
        decision_id = uuid4().hex
        base_url = get_view_url(
            ViolationReportDecisionView.view_name, violation_report_id=violation_report_id, decision_id=decision_id
        )
        decision = ViolationReportDecisionState.create_decision(
            uid=decision_id,
            base_url=base_url,
            violation_report=violation_report,
            data=body.data,
        )
        await update_violation_report(violation_report, modified=False)

        logger.info(
            "Violation Report Decision posted",
            extra=get_request_logging_context({"MESSAGE_ID": "POST_VIOLATION_REPORT_DECISION"}),
        )
        return json_response(
            status=201,
            data={"data": ViolationReportDecisionSerializer(decision).data},
            headers={"Location": url_to_absolute(base_url)},
        )


class DecisionDetailMixing:
    @staticmethod
    def get_decision(violation_report: ViolationReportDBModel, decision_id: str) -> DecisionDBModel:
        for d in violation_report.decisions:
            if d.id == decision_id:
                return d
        else:
            raise JsonHTTPNotFound(details="decision not found.")


class ViolationReportDecisionView(DecisionDetailMixing, BaseView):
    view_name = "violation_report_decision"

    async def get(self, violation_report_id: str, decision_id: str, /) -> r200[DataModel[DecisionDBModel]]:
        """
        Tags: ViolationReports.decisions
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        decision = self.get_decision(violation_report, decision_id)
        return {"data": ViolationReportDecisionSerializer(decision).data}

    async def patch(
        self,
        violation_report_id: str,
        decision_id: str,
        /,
        body: DataModel[Union[DecisionPatchRequestData, DecisionActivateRequestData]],
    ) -> r201[DataModel[DecisionDBModel]]:
        """
        Tags: ViolationReports.decisions
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        decision = self.get_decision(violation_report, decision_id)

        if isinstance(body.data, DecisionActivateRequestData) and decision.status != DraftActiveObjectStatus.active:
            ViolationReportDecisionState.validate_publish_decision(
                violation_report,
                decision,
            )
            ViolationReportDecisionState.publish_decision(
                violation_report=violation_report,
                decision=decision,
            )
            await update_violation_report(violation_report, modified=True)
            logger.info(
                "Violation Report Decision updated",
                extra=get_request_logging_context({"MESSAGE_ID": "VIOLATION_REPORT_DECISION_ACTIVATED"}),
            )

        elif isinstance(body.data, DecisionPatchRequestData):
            ViolationReportDecisionState.validate_update_decision(
                violation_report,
                decision,
            )
            updated_decision = ViolationReportDecisionState.update_decision(
                decision=decision,
                data=body.data,
            )
            if updated_decision:
                await update_violation_report(violation_report, modified=False)
            logger.info(
                "Violation Report Decision updated",
                extra=get_request_logging_context({"MESSAGE_ID": "VIOLATION_REPORT_DECISION_UPDATED"}),
            )
        return {"data": ViolationReportDecisionSerializer(decision).data}


class ViolationReportDecisionDocumentListView(DecisionDetailMixing, BaseView):
    view_name = "violation_report_decision_document_list"

    async def get(self, violation_report_id: str, decision_id: str, /) -> r200[DataModel[List[Document]]]:
        """
        Tags: ViolationReports.decisions
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        decision = self.get_decision(violation_report, decision_id)
        return {"data": [DocumentSerializer(d).data for d in decision.documents]}

    async def post(
        self, violation_report_id: str, decision_id: str, /, body: DataModel[PostDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decisions
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        decision = self.get_decision(violation_report, decision_id)

        ViolationReportDecisionState.validate_post_document(violation_report, decision, body.data)

        base_url = get_view_url(
            ViolationReportDecisionView.view_name, violation_report_id=violation_report_id, decision_id=decision_id
        )
        document = ViolationReportDecisionState.post_document(
            decision,
            body.data,
            base_url=base_url,
        )
        await update_violation_report(violation_report, modified=False)
        logger.info(
            "Violation Report decision document post",
            extra=get_request_logging_context({"MESSAGE_ID": "POST_VIOLATION_REPORT_DECISION_DOCUMENT"}),
        )

        return {"data": DocumentSerializer(document).data}


class ViolationReportDecisionDocumentView(DecisionDetailMixing, BaseView):
    view_name = "violation_report_decision_document"

    async def resolve_document(
        self, violation_report_id: str, decision_id: str, document_id: str, download: Optional[str] = None
    ) -> Tuple[Document, int, DecisionDBModel, ViolationReportDBModel]:
        violation_report = await get_violation_report_or_404(violation_report_id)
        decision = self.get_decision(violation_report, decision_id)
        for doc_index, document in reversed(list(enumerate(decision.documents))):
            if document.id == document_id and (download is None or download in document.url):
                return document, doc_index, decision, violation_report
        else:
            raise HTTPNotFound(text="Document not found.")

    async def get(self, violation_report_id: str, decision_id: str, document_id: str, /) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decisions
        """
        document, *_ = await self.resolve_document(
            violation_report_id, decision_id, document_id, download=self.request.query.get("download")
        )
        if download := self.request.query.get("download"):
            return download_file(
                document=document,
                doc_id=download,
            )
        return {"data": DocumentSerializer(document).data}

    async def patch(
        self, violation_report_id: str, decision_id: str, document_id: str, /, body: DataModel[PatchDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decisions
        """
        document, doc_index, decision, violation_report = await self.resolve_document(
            violation_report_id, decision_id, document_id
        )

        ViolationReportDecisionState.validate_update_decision(violation_report, decision)
        new_document = ViolationReportDecisionState.patch_document(
            decision,
            document=document,
            doc_index=doc_index,
            updates=body.data,
        )
        if new_document:
            await update_violation_report(violation_report, modified=False)
            logger.info(
                "Violation report document patch",
                extra=get_request_logging_context({"MESSAGE_ID": "PATCH_VIOLATION_REPORT_DECISION_DOCUMENT"}),
            )
            return {"data": DocumentSerializer(new_document).data}

        return {"data": DocumentSerializer(document).data}

    async def put(
        self, violation_report_id: str, decision_id: str, document_id: str, /, body: DataModel[PostDocument]
    ) -> r200[DataModel[Document]]:
        """
        Tags: ViolationReports.decisions
        """
        document, doc_index, decision, violation_report = await self.resolve_document(
            violation_report_id, decision_id, document_id
        )

        ViolationReportDecisionState.validate_update_decision(violation_report, decision)

        base_url = get_view_url(
            ViolationReportDecisionView.view_name, violation_report_id=violation_report_id, decision_id=decision_id
        )
        new_document = ViolationReportDecisionState.put_document(
            decision,
            base_url=base_url,
            document_data=body.data,
            document=document,
        )

        await update_violation_report(violation_report, modified=False)
        logger.info(
            "Violation report document put",
            extra=get_request_logging_context({"MESSAGE_ID": "PUT_VIOLATION_REPORT_DECISION_DOCUMENT"}),
        )
        return {"data": DocumentSerializer(new_document).data}

    async def delete(self, violation_report_id: str, decision_id: str, document_id: str, /) -> r204[None]:
        """
        Tags: ViolationReports.decisions
        """
        violation_report = await get_violation_report_or_404(violation_report_id)
        decision = self.get_decision(violation_report, decision_id)

        ViolationReportDecisionState.validate_update_decision(violation_report, decision)

        updated = ViolationReportDecisionState.delete_document(decision, document_id=document_id)
        if updated:
            await update_violation_report(violation_report)
            logger.info(
                "Violation report decision document delete",
                extra=get_request_logging_context({"MESSAGE_ID": "DELETE_VIOLATION_REPORT_DECISION_DOCUMENT"}),
            )
        return HTTPNoContent()
