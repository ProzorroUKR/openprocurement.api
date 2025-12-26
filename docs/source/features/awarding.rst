.. _awarding_approaches:

Awarding approaches (DRAFT)
===========================


CFA UA
------

`cfaua` has common complaintPeriod for all the awards. Here is how it works.

After decisions added to all the awards, tenderer switches tender status from `active.qualification` to `active.qualification.stand-still`.

`awardPeriod.endDate` is calculated as now + 10 days and then assigned to the each award as `complaintPeriod.endDate`

.. sourcecode:: python

    if self.all_awards_are_reviewed(after):
        after["awardPeriod"]["endDate"] = calculate_complaint_business_date(
            get_now(), self.qualification_complaint_stand_still, after
        ).isoformat()
        for award in after["awards"]:
            if award["status"] != "cancelled":
                award["complaintPeriod"] = {
                    "startDate": get_now().isoformat(),
                    "endDate": after["awardPeriod"]["endDate"],
                }


Agreements (Contracts) are added at the end of awardPeriod if there is no complaints.


Default awarding
----------------

In all the other procedures every award has its own unique `complaintPeriod`, based on datetime the decision was posted. Also pending contracts are posted to every(usually only one) `status=active` award.

For the most of the procedures `status=active` award is the last one, so it's decision the latest aw well as the `complaintPeriod.endDate`

Once `complaintPeriod` is over, it's safe to proceed with the contract. But not in the case of :ref:`collective_quantity_tender`.
