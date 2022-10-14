(function() {
  var jQuery = window.jQuery || function() {};

  jQuery(function($) {
    $('.http-example.container').each(function() {
      var $container = $(this),
          $blocks = $(this).children(),
          $captions = $(this).find('.caption').length > 0
            ? $(this).find('.caption')
            : $(this).find('.caption-text').parent().addClass('caption');
      $captions.each(function() {
        var $caption = $(this), $block = $(this).parent();
        $block.attr('role', 'tabpanel').attr('tabindex', '0');
        $block.attr('aria-labelledby', $block.attr('id') + '-label');
        $caption.attr('id', $block.attr('id') + '-label');
        $caption.attr('role', 'tab').attr('tabindex', 0);
        $caption.attr('aria-label', $caption.text().replace(/^\s+|\s+$/g, ''));
        $caption.attr('aria-controls', $block.attr('id'));
        $caption.on('click', function() {
          $captions.not($block.attr('id') + '-label')
            .attr('aria-selected', 'false').removeClass('selected');
          $(this).attr('aria-selected', 'true');
          $(this).addClass('selected');
          $blocks.not($block.attr('id')).hide().attr('hidden', 'hidden');
          $block.show().removeAttr('hidden');
        });
        $caption.on('keydown', function(e) {
          if (event.code === 'Space' || event.code === 'Enter') {
            $caption.click();
          }
        });
        $container.append($caption);
      });
      $container.attr('role', 'tablist');
      $container.append($blocks);
      $captions.first().click();
    });
  });

})();
