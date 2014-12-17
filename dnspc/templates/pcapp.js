var pcApp = angular.module('pcApp', ['checklist-model']);

pcApp.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
  }]);
pcApp.run(function($rootScope) {
    $rootScope.section = 'currrules';
});
