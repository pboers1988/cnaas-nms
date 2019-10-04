import os
import coverage
import atexit
import signal

from cnaas_nms.tools.get_apidata import get_apidata
# Do late imports for anything cnaas/flask related so we can do gevent monkey patch, see below


os.environ['PYTHONPATH'] = os.getcwd()


if 'COVERAGE' in os.environ:
    cov = coverage.coverage(data_file='/coverage/.coverage-{}'.format(os.getpid()))
    cov.start()


    def save_coverage():
        cov.stop()
        cov.save()


    atexit.register(save_coverage)
    signal.signal(signal.SIGTERM, save_coverage)
    signal.signal(signal.SIGINT, save_coverage)


def get_app():
    from cnaas_nms.scheduler.scheduler import Scheduler
    from cnaas_nms.plugins.pluginmanager import PluginManagerHandler
    from cnaas_nms.db.session import sqla_session
    from cnaas_nms.db.joblock import Joblock
    # If running inside uwsgi, a separate "mule" will run the scheduler
    try:
        import uwsgi
        print("Running inside uwsgi")
    except (ModuleNotFoundError, ImportError):
        scheduler = Scheduler()
        scheduler.start()

    pmh = PluginManagerHandler()
    pmh.load_plugins()

    try:
        with sqla_session() as session:
            Joblock.clear_locks(session)
    except Exception as e:
        print("Unable to clear old locks from database at startup: {}".format(str(e)))

    return app.app


if __name__ == '__main__':
    # gevent monkey patching required if you start flask with the auto-reloader (debug mode)
    from gevent import monkey
    monkey.patch_all()
    from cnaas_nms.api import app

    apidata = get_apidata()
    if isinstance(apidata, dict) and 'host' in apidata:
        app.socketio.run(get_app(), debug=True, host=apidata['host'])
    else:
        app.socketio.run(get_app(), debug=True)
else:
    from cnaas_nms.api import app

    cnaas_app = get_app()
