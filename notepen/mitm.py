import asyncio
from mitmproxy import master
from mitmproxy import options
from mitmproxy import flow
from mitmproxy import addons
from mitmproxy.http import HTTPFlow
from mitmproxy.addons import view
from mitmproxy.addons import intercept
from mitmproxy.addons import readfile
from mitmproxy.addons import eventstore
from mitmproxy.addons import errorcheck
from mitmproxy.addons import proxyserver

class NotepenMaster(master.Master):
    def __init__(self, opts: options.Options):
        super().__init__(opts)

        self.view = view.View()
        self.events = eventstore.EventStore()
        self.view.sig_view_add.connect(self._sig_view_add)
        self.view.sig_view_remove.connect(self._sig_view_remove)
        self.view.sig_view_update.connect(self._sig_view_update)
        self.view.sig_view_refresh.connect(self._sig_view_refresh)

        self.addons.add(*addons.default_addons())
        self.addons.add(
            intercept.Intercept(),
            readfile.ReadFile(),
            self.view,
            self.events,
            errorcheck.ErrorCheck(),
        )

        self.proxyserver: proxyserver.Proxyserver = self.addons.get('proxyserver')
        self.proxyserver.servers.changed.connect(self._proxy_server_changed)

    def _proxy_server_changed(self) -> None:
        print(f'servers changed: {self.proxyserver.servers}')

    def _sig_view_add(self, flow: flow.Flow) -> None:
        if isinstance(flow, HTTPFlow):
            print(f'view add: {flow}')
        

    def _sig_view_update(self, flow: flow.Flow) -> None:
        if isinstance(flow, HTTPFlow):
            print(f'view update: {flow}')

    def _sig_view_remove(self, flow: flow.Flow, index: int) -> None:
        if isinstance(flow, HTTPFlow):
            print(f'view remove: {flow} index {index}')

    def _sig_view_refresh(self) -> None:
        print('view refresh')

    async def running(self) -> None:
        print('running...')
        return await super().running()

    """
    def _sig_events_add(self, entry: log.LogEntry) -> None:
        app.ClientConnection.broadcast(
            resource="events", cmd="add", data=app.logentry_to_json(entry)
        )

    def _sig_events_refresh(self) -> None:
        app.ClientConnection.broadcast(resource="events", cmd="reset")

    def _sig_options_update(self, updated: set[str]) -> None:
        options_dict = optmanager.dump_dicts(self.options, updated)
        app.ClientConnection.broadcast(
            resource="options", cmd="update", data=options_dict
        )

    def _sig_servers_changed(self) -> None:
        app.ClientConnection.broadcast(
            resource="state",
            cmd="update",
            data={"servers": [s.to_json() for s in self.proxyserver.servers]},
        )
    """

class Mitm:
    def launch():
        # TODO: handle UI and connect UI to views
        master = NotepenMaster(options.Options())
        event_loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(master.run(), event_loop)