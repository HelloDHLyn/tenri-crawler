'use strict';

const https = require('https');

function request(method, path, data = null) {
  const options = {
    hostname: 'api.lynlab.co.kr',
    port: 443,
    path: path,
    method: method,
    headers: {'x-api-key': process.env.LYNLAB_API_KEY},
    body: data,
    json: true,
  };

  return new Promise((resolve, reject) => {
    let req = https.request(options, res => {
      if (res.statusCode !== 200) {
        reject(new Error(res.statusCode));
      }

      let res_body = '';
      res.on('data', chunk => res_body += chunk);
      res.on('end', () => resolve(JSON.parse(res_body)));
    });

    if (data) {
      req.write(JSON.stringify(data));
    }
    req.on('error', e => reject(e));
    req.end();
  });
}

class KeyValueAPI {
  static getValue(key) {
    return request('GET', `/v1/key_values/${key}`);
  }

  static setValue(key, value) {
    return request('POST', '/v1/key_values', {
      key: key,
      value: value,
    });
  }
}

module.exports.keyValue = KeyValueAPI;
