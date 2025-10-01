(function() {
  var jQuery = window.jQuery || function() {};

  jQuery(function($) {
    // Check if JSON content needs folding
    $('.http-example .json-foldable').each(function() {
      var $container = $(this);
      var $content = $container.find('.json-content');
      var $toggle = $container.find('.json-fold-toggle');
      
      // Temporarily expand to measure full height
      $content.css('max-height', 'none');
      var fullHeight = $content.height();
      
      // If content is short enough, hide the toggle button
      if (fullHeight <= 200) {
        $toggle.hide();
        $container.removeClass('json-foldable');
      } else {
        // Reset to collapsed state
        $content.css('max-height', '200px');
      }
    });

    // JSON folding functionality
    $('.http-example .json-fold-toggle').on('click', function() {
      var $toggle = $(this);
      var $container = $toggle.closest('.json-foldable');
      var $content = $container.find('.json-content');
      
      if ($container.hasClass('expanded')) {
        $container.removeClass('expanded');
        $toggle.removeClass('expanded');
        $toggle.text('Expand');
        $content.css('max-height', '200px'); // Collapse
      } else {
        $container.addClass('expanded');
        $toggle.addClass('expanded');
        $toggle.text('Collapse');
        $content.css('max-height', 'none'); // Expand
      }
    });
  });

})();