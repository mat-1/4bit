document.addEventListener('DOMContentLoaded', () => {

scrolled_up = true
var title_text = document.getElementsByClassName('large-title')[0]
var subtitle_text = document.getElementsByClassName('subtitle')[0]
var invite_btn = document.getElementsByClassName('invite-btn')[0]
var commands_btn = document.getElementsByClassName('cmds-btn')[0]
var header = document.getElementsByTagName('header')[0]
document.onscroll = function(e) {

let scrollTop = e.target.documentElement.scrollTop

title_text.style.transform = 'translate(0px,'+-scrollTop * 0.2+'vh)'

subtitle_text.style.transform = 'translate(0px,'+-scrollTop * 0.1+'vh)'

invite_btn.style.transform = 'translate(0px,'+scrollTop * 0.04 +'vh)'

commands_btn.style.transform = 'translate(0px,'+scrollTop * 0.04+'vh)'

header.style.opacity = 1-scrollTop * 0.0015


if (scrollTop <= 10 && this.oldScroll < scrollTop && scrolled_up) {
	let scroll_to = document.getElementById('commands').offsetTop
	window.scrollBy({ 
		top: scroll_to,
		left: 0, 
		behavior: 'smooth' 
	})
	this.oldScroll = scroll_to;
	scrolled_up = false
} else if (scrollTop >= 10 && this.oldScroll > scrollTop) {
	scrolled_up = true
}
this.oldScroll = scrollTop;
}
})
