// jshint esversion:6

// subscribe is the main function called by Cloud Functions.
module.exports.subscribe = (event, callback) => {
	const build = eventToBuild(event.data.data);

	// Skip if the current status is not in the status list.
	// Add additional statues to list if you'd like:
	// QUEUED, WORKING, SUCCESS, FAILURE,
	// INTERNAL_ERROR, TIMEOUT, CANCELLED
	const status = ['SUCCESS', 'FAILURE', 'INTERNAL_ERROR', 'TIMEOUT'];
	if (status.indexOf(build.status) === -1) {
		return callback();
	}

	// Write status to GCS.
	const text = storageFileContent(build);
	console.log(text);
	callback();
};

// eventToBuild transforms pubsub event message to a build object.
const eventToBuild = (data) => {
	return JSON.parse(new Buffer(data, 'base64').toString());
};

// storageFileContent create content to be stored in GCS.
const storageFileContent = (build) => {
	let message = {
		text: `Build \`${build.id}\``,
		mrkdwn: true,
		attachments: [
			{
				title: 'Build logs',
				title_link: build.logUrl,
				fields: [{
					title: 'Status',
					value: build.status
				}]
			}
		]
	};
	return message;
};
