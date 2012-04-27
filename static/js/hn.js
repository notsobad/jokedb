/* VERSION 1.4 */

if (hn && hn.inited) {
	hn.save();	
} else {
try { if (user_id) {} } catch(e) { user_id = 0; }

var user_id = 1;
function hn() {
	setTimeout('hn.save();', 1);
};
hn.prototype = {

	save : function() 
	{
	
		hn.u = encodeURIComponent(document.location.href);
		hn.t = encodeURIComponent(document.title.replace(/^\s\s*/, '').replace(/\s\s*$/, ''));
			
		if (!user_id) {
			hn.edit();
		} else {
			hn.displayMessage('Saving Page to Read It Later...', true);	
			hn.img = new Image();
			//hn.img.src = 'http://localhost:9527/h='+user_id+'&u='+hn.u+'&t='+hn.t+'&rand='+Math.random();
			hn.img.src = 'http://localhost:9527/api/?v=1&u='+hn.u+'&t='+hn.t+'&rand='+Math.random();
			document.body.appendChild(hn.img);
			hn.int = setInterval('hn.checkImage()', 250);
		}
		
		hn.inited = true;
	},	
	checkImage : function() {	
		return;
		if ( hn.img && hn.img.complete ) {

			clearInterval( hn.int );
			hn.complete = true;		
			
			var w = hn.img.width;
			if (w == 2 || w == 3) {
				var msg = '';//'<div style="padding:20px">';
				if (w == 2) {
					msg += '<p>You are not logged in.  Please log in before saving links to Read It Later</p><p><a target="_blank" href="https://readitlaterlist.com/bl/login/">Login Here</a></p>';
				} else if (w == 3) {
					msg += '<p>Could not save.</p><p>You are not logged into the same account you created the bookmarklet with.<br> Either reinstall the bookmarklet or <a target="_blank" href="https://readitlaterlist.com/bl/login/">relogin</a>.</p><p>If you continue to have problems, <a href="http://www.ideashower.com/support/read-it-later/how-to-install-iphone-bookmarklets/">get help here</a>. ';
				}
				msg += '<p>&nbsp;</p><p><a class="ISRILBTN" style="text-decoration:underline" onclick="hn.hideMessage()">[Close]</a>';
				
				hn.displayMessage(msg);
			} else {
				hn.displayMessage('Page Saved!<br /><br /><small>[<a href="javascript:hn.edit();">Edit item</a>]</small>', true);
				hn.int = setTimeout('hn.hideMessage();', 3000);
			}
			hn.img.style.display = 'none';
			
		}
	},	
	displayMessage : function(m, scale) {
		if (!this.msg) { 
			this.msg = document.createElement( 'div' );
		}
		
		var h = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : document.body.clientHeight;
		
		this.msg.style.cssText = 'display:block;position:absolute;margin:0px;padding:0px;font-size:18px;font-family:Arial;text-align:center;font-size:14px;font-weight:bold;color:#000000;background: #FFFFFF;border:1px solid #333333;z-index:100000;padding:25px';
		document.body.appendChild(this.msg);		
		this.msg.style.fontSize = scale ? (h * 0.06) + 'px' : '18px';
		this.msg.innerHTML = m;
		
		var y = window.pageYOffset ? window.pageYOffset : document.body.scrollLeft;
		var x = window.pageXOffset ? window.pageXOffset : document.body.scrollTop;
		var w = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : document.body.clientWidth;

		this.msg.style.top = ( y + ( h * 0.40 - this.msg.clientHeight / 2 ) ) + 'px';
		this.msg.style.left = ( x + ( w / 2 - this.msg.clientWidth / 2 ) ) + 'px';
	},
	hideMessage : function() {
		this.msg.style.display = 'none';
		this.msg = false;
	},
	
	edit : function() {
		clearInterval(hn.int);
		this.displayMessage('<iframe scrolling="no" style="border:0px;width:300px;height:185px" src="https://readitlaterlist.com/edit?BL=1&url=' + this.u + '&title=' + this.t + '"></iframe><p><small>[<a href="javascript:hn.hideMessage();">Close</a>]</small></p>', true);
		//this.msg.style.padding = '0px';
	}
}

	
var hn = new hn();	
}
void(0);
