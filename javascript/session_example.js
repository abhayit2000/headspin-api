const Session = require("./session.js");

var device_id = 'YOUR_DEVICE_ID';
var host = 'YOUR_HOST';
var status = 'Passed'; // or 'Failed'
var flow_name = 'Transfer 1';
var launch_time = 0.9;
var build = '4.2.1';
const API_KEY = 'YOUR_API_KEY';

var sess = new Session(API_KEY, device_id, host);

sess.start_session();
// Perform tests here
sess.stop_session();
sess.tag_session(status, flow_name, launch_time, build);
