
$(document).ready(function(){
    
    $('.owl-carousel').owlCarousel({
        loop:true,
        margin: 40,
        responsiveClass:true,
        //navContainerClass: "my-nav-class",
        responsive:{
            0:{
                items:1,
                nav:true
            },
            520:{
                items:2,
                nav:false
            },
            700:{
                items:3,
                nav:false
            },
            1000:{
                items:4,
                nav:false,
            },
            1200:{
                items:5,
                nav:false,
            }
        }
    })

});