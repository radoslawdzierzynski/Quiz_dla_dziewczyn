$(function(){
  var rect = $("svg").find("rect")
  var ellipse = $("svg").find("ellipse");
  $("svg").on('click', ()=>{
    rect.toggleClass("checked");
    if(rect.hasClass("checked")){
      TweenLite.to(ellipse, 0.25, {attr: {"cx": 60.911, "rx":1.108, "ry":8.17}})
    } else {
      TweenLite.to(ellipse, 0.25, {attr: {"cx": 28.911, "rx":9.028, "ry": 9.028}})
    }
  })
})