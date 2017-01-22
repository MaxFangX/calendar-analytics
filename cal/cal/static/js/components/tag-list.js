analyticsApp.component('tagList', {
  templateUrl: '/static/templates/tag-list.html',
  controller: ['$scope', '$http', 'CalendarFilterService', 'TagService', TagListCtrl],
  bindings: {
    isCumulative: '<?',
    displayName: '@',
    hideZeroHours: '<?'
  }
});

function TagListCtrl($scope, $http, CalendarFilterService, TagService) {

  var _this = this;

  this.tags = [];
  this.tags.dataLoaded = false;

  $scope.$on('calendarFilter:updated', function(event, data) {
    /* jshint unused:vars */
    _this.tags.dataLoaded = false;
    var filterData = CalendarFilterService.getFilter();
    if (!_this.isCumulative) {
      TagService.getTags(filterData.filterKey, filterData.start, filterData.end,
                         filterData.calendarIds)
        .then(function(tags) {
          _this.tags = tags;
          _this.filterKey = filterData.filterKey;
          _this.tags.dataLoaded = true;
        });
    } else {
      TagService.getTags('cumulative ' + filterData.filterKey, null, null,
                         filterData.calendarIds)
        .then(function(tags) {
          _this.tags = tags;
          _this.tags.dataLoaded = true;
        });
    }
  });

  this.hideZeroHoursFilter = function (value, index, array) {
    /* jshint unused:vars */
    return !(_this.hideZeroHours && value.hours === 0);
  };

  this.create = function(tag) {
    var filterData = CalendarFilterService.getFilter();
    TagService.createTag(tag.label, tag.keywords, this.isCumulative, filterData)
      .success(function addToList(data) {
        _this.tags.push({
          id: data.id,
          label: data.label,
          keywords: data.keywords,
          hours: data.hours,
          editing: false
        });
      _this.tags.dataLoaded = true;
      });
  };

  this.startEdit = function(tagId) {
    var tag = this.tags.find(function(tag, index, array) {
      /* jshint unused:vars */
      return tag.id == tagId;
    });
    tag.newLabel = tag.label;
    tag.newKeywords = tag.keywords;
    tag.editing = true;
  };

  this.submitEdit = function(tagId) {
    var filterData = CalendarFilterService.getFilter();
    var tag = this.tags.find(function(tag, index, array) {
      /* jshint unused:vars */
      return tag.id == tagId;
    });
    tag.editing = false;
    TagService.editTag(tagId, tag.newLabel, tag.newKeywords, this.isCumulative, filterData)
      .then(function(returnedTag) {
        tag.label = returnedTag.label;
        tag.keywords = returnedTag.keywords;
        tag.hours = returnedTag.hours;
      });
  };

  this.cancelEdit = function(tagId) {
    var tag = this.tags.find(function(tag, index, array) {
      /* jshint unused:vars */
      return tag.id == tagId;
    });
    tag.editing = false;
  };

  this.delete = function(tagId) {
    TagService.deleteTag(tagId)
      .success(function removeFromList() {
        _this.tags = _this.tags.filter(function(tag) {
          return tag.id !== tagId;
        });
        _this.tags.dataLoaded = true;
      });
  };
}
