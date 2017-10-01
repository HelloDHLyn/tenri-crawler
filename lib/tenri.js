'use strict';

const aws = require('aws-sdk');
aws.config.update({region: 'ap-northeast-2'});

const sns = new aws.SNS();

function sendMessage(body) {
  const params = {
    TopicArn: `${process.env.TOPIC_ARN}:tenri_send_message`,
    Message: body
  };

  sns.publish(params, (err, data) => {
    if (err) {
      console.error(err, err.stack);
    } else {
      console.log(data);
    }
  });
}

module.exports = {};
module.exports.sendMessage = sendMessage;
