from ryu.lib import hub

class Timer(object):
    def __init__(self, handler_):
        assert callable(handler_)

        super(Timer, self).__init__()
        self._handler = handler_
        self._event = hub.Event()
        self._thread = None

    def start(self, interval):
        """interval is in seconds"""
        if self._thread:
            self.cancel()
        self._event.clear()
        print "spawning _timer"
        self._thread = hub.spawn(self._timer, interval)

    def cancel(self):
        if self._thread is None:
            return
        self._event.set()
        hub.joinall([self._thread])
        self._thread = None

    def is_running(self):
        return self._thread is not None

    def _timer(self, interval):
        # Avoid cancellation during execution of self._callable()
        cancel = self._event.wait(interval)
        if cancel:
            print "_timer cancel"
            return
        print "_timer: self.handler()"
        self._handler()

class TimerEventSender(Timer):
    # timeout handler is called by timer thread context.
    # So in order to actual execution context to application's event thread,
    # post the event to the application
    def __init__(self, app, ev_cls):
        super(TimerEventSender, self).__init__(self._timeout)
        self._app = app
        self._ev_cls = ev_cls

    def _timeout(self):
        print "TimerEventSender._timeout()"
        print "Event Class:",self._ev_cls
        print " app:",self._app
        print "name:",self._app.name
        self._app.send_event(self._app.name, self._ev_cls())

