analyticsApp.component('categoryList', {
  templateUrl: '/static/js/components/category-list/category-list.html',
  controller: ['$scope', '$http', 'CalendarFilterService', 'CategoryService', CategoryListCtrl],
  controllerAs: '$ctrl',
  bindings: {
    isCumulative: '<?',
    displayName: '@',
    hideZeroHours: '<?'
  }
});

function CategoryListCtrl($scope, $http, CalendarFilterService, CategoryService) {

  var _this = this;

  this.categories = [];
  this.categories.dataLoaded = false;

  $scope.$on('calendarFilter:updated', function(event, data) {
    /* jshint unused:vars */
    _this.categories.dataLoaded = false;
    var filterData = CalendarFilterService.getFilter();
    if (!_this.isCumulative) {
      CategoryService.getCategories(filterData.filterKey, filterData.start,
        filterData.end, filterData.calendarIds)
        .then(function(categories) {
          _this.categories = categories;
          _this.filterKey = filterData.filterKey;
          _this.categories.dataLoaded = true;
        });
    } else {
      CategoryService.getCategories('cumulative ' + filterData.filterKey, null,
        null, filterData.calendarIds)
        .then(function(categories) {
          _this.categories = categories;
          _this.categories.dataLoaded = true;
        });
    }
  });

  this.hideZeroHoursFilter = function(value, index, array) {
    /* jshint unused:vars */
    return !(_this.hideZeroHours && value.hours === 0);
  };

  this.startEdit = function(categoryId) {
    var category = _this.categories.find(function(category, index, array) {
      /* jshint unused:vars */
      return category.id == categoryId;
    });
    category.newLabel = category.label;
    category.editing = true;
  };

  this.submitEdit = function(categoryId) {
    var category = _this.categories.find(function(category, index, array) {
      /* jshint unused:vars */
      return category.id == categoryId;
    });
    category.editing = false;

    CategoryService.editCategory(categoryId, category.newLabel)
      .then(function(returnedCategory) {
        category.label = returnedCategory.label;
        _this.categories.dataLoaded = true;
      });
  };

  this.cancelEdit = function(categoryId) {
    var category = this.categories.find(function(category, index, array) {
      /* jshint unused:vars */
      return category.id == categoryId;
    });
    category.editing = false;
  }.bind(this);

  this.delete = function(categoryId) {
    CategoryService.deleteCategory(categoryId)
      .then(function removeFromList(data) {
        /* jshint unused:vars */
        _this.categories = _this.categories.filter(function(category) {
          return category.id !== categoryId;
        });
      _this.categories.dataLoaded = true;
      });
  };

  // categories pie chart
  this.categoryPie = {
    chart: {
      type: 'pieChart',
      height: 200,
      x: function(d){return d.label;},
      y: function(d){return d.hours;},
      showLabels: false,
      growOnHover: true,
      duration: 500,
      labelThreshold: 0.01,
      labelSunbeamLayout: true,
      showLegend: false
    },
  };
}

