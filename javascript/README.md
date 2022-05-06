# Headspin API - Javascript

Integrate `session.js` into automation code to start, stop and tag a Headspin recording session.

## Requirements

Javascript libraries:

`npm i request`

`npm i sync-request`

## Usage

Import the package with:

`const Session = require("./session.js");`

Initialize the session with:

`var sess = new Session(API_KEY, device_id, host);`

Then use the following to start, stop and tag a session:

`sess.start_session();`

`sess.stop_session();`

`sess.tag_session(status, flow_name, launch_time, build);`

A worked example can be found in `session_example.js`. Please substitute your own Headspin device ID, hostname and API key.
