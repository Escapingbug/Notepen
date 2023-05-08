import asyncio
import ipyvuetify as v
from notepen.ui import mitm as mitm_ui
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

from IPython.display import display

class NotepenMaster(master.Master):
    def __init__(self, opts: options.Options, ui: mitm_ui.Mitm):
        super().__init__(opts)

        self.ui = ui
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

    def flow_to_info(self, flow: HTTPFlow) -> dict:
        time = ''
        if flow.request.timestamp_end:
            time = flow.request.timestamp_end - flow.request.timestamp_start
        return {
            'id': flow.id,
            'host': flow.request.host,
            'path': flow.request.path,
            'method': flow.request.method,
            'status': flow.response.status_code if flow.response else '',
            'size': len(flow.response.content) if flow.response else '',
            'time': time,
        }

    def _sig_view_add(self, flow: flow.Flow) -> None:
        if isinstance(flow, HTTPFlow):
            print(f'view add: {flow}')
            self.ui.proxy_view.ui.items.append(
                self.flow_to_info(flow)
            )
            self.ui.proxy_view.ui.set_state({
                'items': self.ui.proxy_view.ui.items
            })
        

    def _sig_view_update(self, flow: flow.Flow) -> None:
        if isinstance(flow, HTTPFlow):
            print(f'view update: {flow}')
            for i in range(len(self.ui.proxy_view.ui.items)):
                item = self.ui.proxy_view.ui.items[i]
                if item['id'] == flow.id:
                    self.ui.proxy_view.ui.items[i] = self.flow_to_info(flow)
                    break

            self.ui.proxy_view.ui.set_state({
                'items': self.ui.proxy_view.ui.items
            })

    def _sig_view_remove(self, flow: flow.Flow, index: int) -> None:
        if isinstance(flow, HTTPFlow):
            for i in range(len(self.ui.proxy_view.ui.items)):
                item = self.ui.proxy_view.ui.items[i]
                if item['id'] == flow.id:
                    del self.ui.proxy_view.ui.items[i]
                    break

            self.ui.proxy_view.ui.set_state({
                'items': self.ui.proxy_view.ui.items
            })

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
    async def launch():
        # TODO: handle UI and connect UI to views
        ui = mitm_ui.Mitm()
        master = NotepenMaster(options.Options(), ui)

        def on_stop(widget, event, data):
            # TODO: mitmproxy is not stopped somehow even if
            # shutdown is called. Even directly in ipynb, 
            # cancel the proxy run then call shutdown is not
            # working. How to fix this?
            """
            ui.buttons.start_button.ui.children = [
                v.Icon(left=True, children=["mdi-play"]),
                "Begin"
            ]
            ui.buttons.start_button.ui.set_state({
                "color": "success"
            })
            ui.buttons.start_button.ui.on_event('click', on_begin)
            master.shutdown()
            """
            
        def on_begin(widget, event, data):
            ui.buttons.start_button.ui.children = [
                v.Icon(left=True, children=["mdi-stop"]),
                "Stop"
            ]
            ui.buttons.start_button.ui.set_state({
                "color": "error"
            })
            ui.buttons.start_button.ui.on_event('click', on_stop)
            asyncio.get_event_loop().create_task(
                master.run()
            )

        ui.buttons.start_button.ui.on_event('click', on_begin)
        display(ui.ui)