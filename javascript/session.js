const async_request = require('request');
const sync_request = require('sync-request');

module.exports = class Session {
  constructor(api_token, device_id, host) {
    this.api_token = api_token;
    this.device_address = device_id.concat('@',host);
  }

  start_session() {

    var res = sync_request('POST', "https://api-dev.headspin.io/v0/sessions", {
      headers: {
        'Authorization': 'Bearer '.concat(this.api_token) 
      },
      json: {
        "device_address": this.device_address,
        "session_type" : "capture"}
    });
    this.session_id = JSON.parse(res.getBody('utf8')).session_id;
    console.log(this.session_id);
  };

  _callback(error, response, body) {
    console.error('error:', error); // Print the error if one occurred
    console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
    console.log('body:', body); 
  };

  stop_session() {

    async_request.patch('https://api-dev.headspin.io/v0/sessions'.concat('/',this.session_id), {
      'auth': {
        'bearer': this.api_token
      },
      'json': {'active': false}},
      this._callback);
  }

  tag_session(status, flow_name, launch_time, build) {

    var session_data = {
      'session_id': this.session_id,
      'status': status,
      'test_name': flow_name,
      'data' : [{'key': 'Launch Time', 'value': launch_time}]
    };

    async_request.post("https://api-dev.headspin.io/v0/perftests/upload", {
      'auth': {
        'bearer': this.api_token
      },
      'json': session_data},
      this._callback);

    var tag_url = "https://api-dev.headspin.io/v0/sessions/tags/".concat(this.session_id);
    var tags = 
      [{'build': build}]
    ;

    async_request.post(tag_url, {
      'auth': {
        'bearer': this.api_token 
      },
      'json': tags},
      this._callback);
  }

};

