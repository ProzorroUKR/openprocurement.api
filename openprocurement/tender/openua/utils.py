def get_invalidated_bids_data(request):
    data = request.validated['data']
    tender = request.validated['tender']
    data['bids'] = []
    for bid in tender.bids:
        if bid.status != "deleted":
            bid.status = "invalidBid"
        data['bids'].append(bid.serialize())
    return data
