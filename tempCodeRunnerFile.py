kitchen_thread = Thread(target=lambda: app.run(host = '0.0.0.0', port = 8000, debug = False, use_reloader = False), daemon = True)
    kitchen_thread.start()