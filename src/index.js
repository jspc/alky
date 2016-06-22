var async = require("async");
var aws = require('aws-sdk');


exports.create = function(event, context, callback){
    async.waterfall([
        async.apply(connectToGoogle, loginObj),
        getSAMLResponse,
        connectToAWS,
        getToken
    ]);

    callback();
};

var connectToGoogle = function(loginObj, callback){

};

exports.create({}, {}, function(){console.log('done');});
