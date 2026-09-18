self.addEventListener("notificationclick", event => {
    event.notification.close();
    event.waitUntil(clients.matchAll({type:"window",includeUncontrolled:true}).then(list => {
        const client = list.find(item => "focus" in item);
        return client ? client.focus() : clients.openWindow("/student.html");
    }));
});
