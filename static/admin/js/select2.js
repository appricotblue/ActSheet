(function($) {
  'use strict';

  if ($(".js-example-basic-single").length) {
    $(".js-example-basic-single").select2();
  }

  if ($(".js-example-basic-multiple").length) {
    $(".js-example-basic-multiple").select2();
  }

  // ------select2 ---- 
  if ($("#js-select").length) {
    $("#js-select").select2();
  }

  if ($("#js-select1").length) {
    $("#js-select1").select2();
  }

  if ($("#js-select2").length) {
    $("#js-select2").select2();
  }

})(jQuery);