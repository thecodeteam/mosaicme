$(document).ready(function(){
	$("#carousel1").tiksluscarousel(
		{
			width:0,
			height:0,
			nav:'thumbnails',
			current:1,
			autoplayInterval:5000,
			loader: 'static/images/ajax-loader.gif'
		});
});