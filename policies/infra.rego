package infra

default allow := false

allow if {
    input.action == "deploy"
    input.host.disk_free_gb >= 10
    input.host.cpu_load <= 2.0
}

reason := "Insufficient disk space or high CPU load" if {
    input.action == "deploy"
    not allow
}
