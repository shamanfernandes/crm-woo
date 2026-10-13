<?php add_filter('http_request_host_is_external', '__return_true');
add_filter('http_request_args', function($args){$args['reject_unsafe_urls']=false;return $args;});
