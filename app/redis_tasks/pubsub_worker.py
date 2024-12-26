
def handle_order_expiration():
    from app import app
    with app.app_context():
        from app import dao, models, redis_client
        pubsub = redis_client.pubsub()
        pubsub.psubscribe('__keyevent@0__:expired')
        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                expired_key = message['data']
                order = dao.get_order_by_id(expired_key)
                dao.change_status_order(order, order.create_date, models.OrderStatus.FAILED)
                dao.import_into_inventory(order.order_details)