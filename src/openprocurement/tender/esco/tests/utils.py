def prepare_items(data):
    for item in data["items"]:
        del item["unit"]
        del item["quantity"]
        del item["deliveryDate"]
