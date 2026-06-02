def run(alert_queue):
    while True:
        alert = alert_queue.get()
        if alert is None:
            break
        print(f"ALERT: Person detected | Camera: {alert['camera']} | Confidence: {alert['confidence']:.2f} | Track ID: {alert['track_id']} | Time: {alert['Timestamp']}")