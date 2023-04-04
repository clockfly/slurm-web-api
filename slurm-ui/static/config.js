var apiUrl = {
  users : "/users",
  history : "/history",
  queue : "/queue",
  partitions : "/partitions",
  nodes : "/nodes",
  stats : "/stats"
};

var currentIP = window.location.hostname;
var queueStatusUrl = "http://" + currentIP + ":3000/d-solo/8Y16qWYVk/slurm-dashboard?orgId=1&refresh=30s&theme=light&panelId=2&from=now-12h";

