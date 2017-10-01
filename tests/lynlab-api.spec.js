'use strict';

const expect = require('chai').expect;

const lynapi = require('./../lib/lynlab-api');

describe('lynlab-api', () => {
  describe('KeyValue', () => {
    it('set', done => {
      lynapi.keyValue.setValue('PING', 'pong').then(() => {
        done();
      }).catch(e => done(e));
    });

    it('get', done => {
      lynapi.keyValue.getValue('PING').then(res => {
        expect(res.value).to.equal('pong');
        done();
      }).catch(e => done(e));
    });
  })
});
