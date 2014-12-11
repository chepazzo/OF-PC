var pcApp = angular.module('pcApp', []);

pcApp.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
  }]);

pcApp.controller('HostCtrl', function ($scope,$http) {

    $scope.newhost = {
        "name":"{{hostname}}",
        "ip":"{{ip}}",
        "mac":"{{mac}}",
        "owner":""
    };

    $scope.add_host = function(data) {
        var url = '{{url_for('addhost')}}';
        var method = 'POST';
        $http(
            {method: method, url: url,data: JSON.stringify(data)}
        ).success(function(data, status) {
            $scope.get_hosts();
        }).error(function(data, status) {
            console.log('ERROR');
            console.log(data);
            console.log(status);
        });
    };
    $scope.del_host = function(uid) {
        var data = {'uid':uid};
        var url = '{{url_for('delhost')}}';
        var method = 'POST';
        $http(
            {method: method, url: url,data: JSON.stringify(data)}
        ).success(function(data, status) {
            //gotDel(data,status);
            $scope.get_hosts();
        }).error(function(data, status) {
            console.log('ERROR');
            console.log(data);
            console.log(status);
        });
    };
    $scope.get_hosts = function() {
        var url = '{{url_for('get_hosts')}}';
        var method = 'GET';
        $http(
            {method: method, url: url}
        ).success(function(data, status) {
            //gotRules(data,status);
            $scope.myhosts = data.data;
            console.log(data.data);
        }).error(function(data, status) {
            console.log('ERROR');
            console.log(data);
            console.log(status);
        });
    };

    $scope.sort = { 'column':'name','descending': false };

    $scope.changeSorting = function(column) {
        var sort = $scope.sort;

        if (sort.column == column) {
            sort.descending = !sort.descending;
        } else {
            sort.column = column;
            sort.descending = false;
        }
    };

    $scope.get_hosts();
});

pcApp.filter('stripdomain', function () {
  return function (item) {
      //console.log('stripdomain');
      //console.log(item);
      return item.split(".")[0];
  };
});
