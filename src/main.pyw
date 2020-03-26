from methods import AutoElectricMeter

if __name__ == '__main__':
    app = AutoElectricMeter()
    app.start()
    if(app.usingDB):
        app.connection.close()