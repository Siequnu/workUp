$(document).ready(function () {
    $('.btn-filter').on('click', function () {
      var $target = $(this).data('target');
      if ($target != 'all') {
        $('#searchableTable tr').css('display', 'none');
        $('#searchableTable tr[data-status="' + $target + '"]').fadeIn('slow');
      } else {
        $('#searchableTable tr').css('display', 'none').fadeIn('slow');
      }
    });

 });