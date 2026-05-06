package canary

default allow := false

allow if {
    input.action == "promote"
    input.promote_to == "canary"
    input.metrics.error_rate <= 0.01
    input.metrics.p99_latency_ms <= 500
}

reason := "High error rate or latency in canary" if {
    input.action == "promote"
    input.promote_to == "canary"
    not allow
}
