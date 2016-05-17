(function($) {

	skel.breakpoints({
		wide: '(max-width: 1680px)',
		normal: '(max-width: 1280px)',
		narrow: '(max-width: 980px)',
		narrower: '(max-width: 840px)',
		mobile: '(max-width: 736px)'
	});

	$(function() {
    //var preloader = $('.preloader');

		var	$window = $(window),
			$body = $('body'),
			$header = $('#header'),
			$banner = $('#banner'),
			$sidebar = $('#sidebar');

		// Disable animations/transitions until the page has loaded.
			$body.addClass('is-loading');
      $('.caption').addClass('invisible');
      $('#header').addClass('invisible');

    // Background placement for mobile.
      jQuery(window).resize('resizeBackground');
      function resizeBackground() {
          var wheight = jQuery(window).height();
          $banner.height(wheight);
          $('.caption').css({top: wheight * 0.45});
          $('.fa-angle-down').css({top: wheight - 50});
          /*
          console.log('resized to ' + wheight);
          console.log('topped to ' + wheight * 0.45);
          */

      }

      function getMobileOperatingSystem() {
        var userAgent = navigator.userAgent || navigator.vendor || window.opera;

        if( userAgent.match( /iPad/i ) || userAgent.match( /iPhone/i ) || userAgent.match( /iPod/i ) )
        {
          return 'iOS';

        }
        else if( userAgent.match( /Android/i ) )
        {

          return 'Android';
        }
        else
        {
          return 'unknown';
        }
      }

			$window.on('load', function() {
				$body.removeClass('is-loading');
        $('.caption').removeClass('invisible');
        $('#header').removeClass('invisible');
// If desktop: background-attachment: fixed.
// If Android: background-attachment: fixed. (Will auto become scroll).
// If iOS: background-attachment: scroll.
        var os = getMobileOperatingSystem();
        if (os == 'iOS') {
          $('#banner').css('background-attachment', 'scroll'); 
          $('#wedding').css('background-attachment', 'scroll'); 
          resizeBackground();
        }
        if (os == 'Android') {
          resizeBackground();
        }
        //preloader.remove();
			});

		// CSS polyfills (IE<9).
			if (skel.vars.IEVersion < 9)
				$(':last-child').addClass('last-child');

		// Fix: Placeholder polyfill.
			$('form').placeholder();

		// Prioritize "important" elements on narrower.
			skel.on('+narrower -narrower', function() {
				$.prioritize(
					'.important\\28 narrower\\29',
					skel.breakpoint('narrower').active
				);
			});


		// Sidebar.
			if ($sidebar.length > 0) {

				var $sidebar_a = $sidebar.find('a');

				$sidebar_a
					.addClass('scrolly')
					.on('click', function() {

						var $this = $(this);

						// External link? Bail.
							if ($this.attr('href').charAt(0) != '#')
								return;

						// Deactivate all links.
							$sidebar_a.removeClass('active');

						// Activate link *and* lock it (so Scrollex doesn't try to activate other links as we're scrolling to this one's section).
							$this
								.addClass('active')
								.addClass('active-locked');

					})
					.each(function() {

						var	$this = $(this),
							id = $this.attr('href'),
							$section = $(id);

						// No section for this link? Bail.
							if ($section.length < 1)
								return;

						// Scrollex.
							$section.scrollex({
								mode: 'middle',
                /*
								top: '-20vh',
                */
								bottom: '-20vh',
								initialize: function() {

									// Deactivate section.
										if (skel.canUse('transition'))
											$section.addClass('inactive');

								},
								enter: function() {

									// Activate section.
										$section.removeClass('inactive');

									// No locked links? Deactivate all links and activate this section's one.
										if ($sidebar_a.filter('.active-locked').length == 0) {

											$sidebar_a.removeClass('active');
											$this.addClass('active');

										}

									// Otherwise, if this section's link is the one that's locked, unlock it.
										else if ($this.hasClass('active-locked'))
											$this.removeClass('active-locked');

								}
							});

					});

			}
		// Dropdowns.
			$('#nav > ul').dropotron({
				mode: 'fade',
				noOpenerFade: true,
				expandMode: (skel.vars.touch ? 'click' : 'hover')
			});

		// Off-Canvas Navigation.

			// Navigation Button.
				$(
					'<div id="navButton">' +
						'<a href="#navPanel" class="toggle"></a>' +
					'</div>'
				)
					.appendTo($body);

			// Navigation Panel.
				$(
					'<div id="navPanel">' +
						'<nav>' +
							$('#nav').navList() +
						'</nav>' +
					'</div>'
				)
					.appendTo($body)
					.panel({
						delay: 500,
						hideOnClick: true,
						hideOnSwipe: true,
						resetScroll: true,
						resetForms: true,
						side: 'left',
						target: $body,
						visibleClass: 'navPanel-visible'
					});

			// Fix: Remove navPanel transitions on WP<10 (poor/buggy performance).
				if (skel.vars.os == 'wp' && skel.vars.osVersion < 10)
					$('#navButton, #navPanel, #page-wrapper')
						.css('transition', 'none');

		// Scrolly links.
			$('.scrolly').scrolly({
				speed: 1000,
				offset: function() {
/*
						if ($sidebar.length > 0 && !$header.hasClass('alt'))
              console.log("HEAD:");
							return $header.height();

          console.log("-1");
*/
					return -1;

				}
			});
			$('.weddingscrolly').scrolly({
				speed: 1000,
				offset: function() {

/*
						if ($sidebar.length > 0 && !$header.hasClass('alt'))
              console.log("HEAD:");
							return $header.height();

          console.log("-1");
*/
					return -100;

				}
			});
			$('.travelscrolly').scrolly({
				speed: 1000,
				offset: function() {

/*
						if ($sidebar.length > 0 && !$header.hasClass('alt'))
              console.log("HEAD:");
							return $header.height();

          console.log("-1");
*/
					return 40;

				}
			});

		// Poptrox.
			$('.story-gallery').poptrox({
				useBodyOverflow: false,
				overlayOpacity: (skel.vars.IEVersion < 9 ? 0 : 0.75),
        /*
				usePopupEasyClose: false,
				overlayColor: '#0a1919',
				usePopupDefaultStyling: false,
				usePopupCaption: true,
				usePopupNav: true
        */
        baseZIndex: 99999,
				popupLoaderText: '',
				windowMargin: 10,
      });
			$('.gallery').poptrox({
				useBodyOverflow: false,
				overlayOpacity: (skel.vars.IEVersion < 9 ? 0 : 0.75),
        /*
				usePopupEasyClose: false,
				overlayColor: '#0a1919',
				usePopupDefaultStyling: false,
				usePopupCaption: true,
        */
        baseZIndex: 99999,
				popupLoaderText: '',
				windowMargin: 10,
				usePopupNav: true
			});

		// Header.
		// If the header is using "alt" styling and #banner is present, use scrollwatch
		// to revert it back to normal styling once the user scrolls past the banner.
		// Note: This is disabled on mobile devices.
			if (!skel.vars.mobile
			&&	$header.hasClass('alt')
			&&	$banner.length > 0) {

				$window.on('load', function() {

					$banner.scrollwatch({
						delay:		0,
						range:		1,
						anchor:		'top',
						on:			function() { $header.addClass('alt reveal'); },
						off:		function() { $header.removeClass('alt'); }
					});

				});

			}

	});

})(jQuery);
