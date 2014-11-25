function PC($scope,$http) {
    $scope.add_rule = function(data) {
        var url = '{{url_for('addrule')}}';
        var method = 'POST';
        $http(
            {method: method, url: url,data: JSON.stringify(data)}
        ).success(function(data, status) {
            gotPlay(data,status);
        }).error(function(data, status) {
            gotPlay(data,status);
        });
    };
    $scope.del_rule = function(uid) {
        var data = {'uid':uid};
        var url = '{{url_for('delrule')}}';
        var method = 'POST';
        $http(
            {method: method, url: url,data: JSON.stringify(data)}
        ).success(function(data, status) {
            gotPlay(data,status);
        }).error(function(data, status) {
            gotPlay(data,status);
        });
    };
    $scope.get_rules = function() {
        var url = '{{url_for('get_rules')}}';
        var method = 'GET';
        $http(
            {method: method, url: url}
        ).success(function(data, status) {
            gotRules(data,status);
        }).error(function(data, status) {
            gotRules(data,status);
        });
    };
}

