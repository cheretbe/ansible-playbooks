def set_local_package_cache_host(config, hostname)
  unless hostname.to_s.strip.empty?
    config.vm.provision "shell",
      name: "Set local package cache for apt and pip",
      keep_color: true, privileged: true,
      path: (File.dirname(__FILE__) + "/local_package_cache.sh"),
      args: hostname.to_s.strip
  end
end