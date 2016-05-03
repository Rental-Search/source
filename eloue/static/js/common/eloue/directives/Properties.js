define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    "use strict";
    
    EloueCommon.directive('elouePropertyDropdown', function(){
        return {
          template: '<select ng-model="model" '+
                      'ng-options="choice for choice in proto.choices" '+
                      'data-placeholder="{{proto.name}}" '+
                      'class="form-control" eloue-chosen></select>',
          restrict: 'A',
          scope: {
              proto: '=propertyType', 
              product: '='
          },
          controller: ['$scope', '$element', '$attrs', '$log', function ($scope, $element, $attrs, $log) {
              
              //$log.debug($scope);
              
              var init = $scope.product[$scope.proto.attr_name];
              
              $scope.model = init ? init : $scope.proto.default;
              
              $scope.$watch('model', function (newVal, oldVal, scope) {
                  scope.product[scope.proto.attr_name] = newVal;
              });
              
              $scope.$watch('product.'+$scope.proto.attr_name, function (newVal, oldVal, scope) {
                  scope.model = newVal;
              });
              
          }]
        };
    });
    
});