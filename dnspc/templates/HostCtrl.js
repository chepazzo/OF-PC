pcApp.controller('HostCtrl', function ($scope,$rootScope,$http) {

    $scope.issection = function(sect) {
        if ($rootScope.section == sect) { return true; }
        return false;
    };
    $scope.setsection = function(sect) {
        $rootScope.section = sect;
    };
    $scope.newhost = {
        "name":"",
        "ip":"",
        "mac":"",
        "owner":""
    };
    $scope.myhost = {
        "name":"{{hostname}}",
        "ip":"{{ip}}",
        "mac":"{{mac}}",
        "owner":""
    };
    $scope.edit_host = function(host) {
        $scope.newhost = host;
    };
    $scope.save_host = function(data) {
        var url = '{{url_for('savehost')}}';
        var method = 'POST';
        $http(
            {method: method, url: url,data: JSON.stringify(data)}
        ).success(function(data, status) {
            $scope.get_hosts();
            $scope.resetnewhost();
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
            $scope.allhosts = data.data;
            for (var i=0; i<$scope.allhosts.length; i++) {
                host = $scope.allhosts[i];
                if (host['mac'] == '{{mac}}') {
                    $scope.myhost._uid = host._uid;
                    $scope.myhost.owner = host.owner;
                    //$scope.myhost = host;
                    break;
                }
            }
            console.log(data.data);
        }).error(function(data, status) {
            console.log('ERROR');
            console.log(data);
            console.log(status);
        });
    };
    $scope.resetnewhost = function() {
        $scope.newhost = {
            "name":"",
            "ip":"",
            "mac":"",
            "owner":""
        };
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
