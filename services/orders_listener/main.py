import functions_framework

@functions_framework.cloud_event
def orders_listener(cloud_event):
    # mock: just log and exit
    print("orders_listener triggered")
