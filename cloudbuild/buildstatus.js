// jshint esversion:6
//
// Testing
// -------
// url:   https://console.cloud.google.com/functions/details/us-central1/subscribe?tab=testing
// cli:   echo '{"status":"SUCCESS"}' | base64
// event: {"data": "eyJzdGF0dXMiOiJTVUNDRVNTIn0K"}

const fs  = require('fs');
const storage = require('@google-cloud/storage')();

const green  = '#4c1';
const red    = '#e05d44';
const yellow = '#dfb317';
const gray   = 'gray';

const chain = (funcs, cb) => {
	let i = 0, fn;
	const proc = (err) => {
		if (err) cb(err);
		else {
			fn = funcs[i++];
			if (fn) fn(proc);
			else    cb();
		}
	};
	proc();
};

// subscribe is the main function called by Cloud Functions.
module.exports.subscribe = (event, callback) => {
	if (event.data.data === undefined) {
		// use dummy event for testing
		event.data.data = 'eyJzdGF0dXMiOiJTVUNDRVNTIn0K';
	}
	const build = eventToBuild(event.data.data);

	// Skip if the current status is not in the status list.
	// Add additional statues to list if you'd like:
	// QUEUED, WORKING, SUCCESS, FAILURE,
	// INTERNAL_ERROR, TIMEOUT, CANCELLED
	let color = gray;
	let text  = 'unknown';
	switch (build.status) {
		case 'INTERNAL_ERROR':
		case 'TIMEOUT':
		case 'FAILURE': color = red;    text = 'failed';  break;
		case 'SUCCESS': color = green;  text = 'passing'; break;
		case 'WORKING':
		case 'QUEUED':  color = yellow; text = 'pending'; break;
		default:        color = gray;   text = 'unknown';
	}


	const bucket   = storage.bucket('ubunatic-public');
	const svgFile  = bucket.file('makepy/build-status.svg');
	const dataFile = bucket.file('makepy/build-status.json');
	const svgPath  = 'build-status.svg';

	let json, svg;
	try       { json = JSON.stringify(storageFileData(build)); }
   catch (e) { json = '{"status": "STATUS_ERROR"}'; }

	chain([
		(cb) => { fs.readFile(svgPath, 'utf8', (err, buf) => { svg = buf; cb(err); }); },
		(cb) => {
			svg = svg.toString().replace(/green/g, color).replace(/STATUS/g, text);
			console.log({
				project: process.env.GCLOUD_PROJECT,
				build:   build,
				svg:     svg,
				json:    json,
			});
			cb();
		},
		(cb) => { svgFile.save( svg,  {metadata: {contentType: 'image/svg+xml'}},    cb); },
		(cb) => { dataFile.save(json, {metadata: {contentType: 'application/json'}}, cb); },
	],	(err) => {
		if (err) console.error('failed to save build status:', err);
		callback();
	});
};

// eventToBuild transforms pubsub event message to a build object.
const eventToBuild = (data) => {
	return JSON.parse(new Buffer(data, 'base64').toString());
};

// storageFileContent create content to be stored in GCS.
const storageFileData = (build) => {
	let data = {
		id:     build.id,
		status: build.status
	};
	return data;
};
