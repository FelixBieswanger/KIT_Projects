const fm = FileManager.local();
const user = "USERNAME"

const widget = new ListWidget();
widget.backgroundColor = Color.white();
await createWidget();
var smallfont = new Font("r", 10);
Script.setWidget(widget);
widget.presentSmall()
Script.complete();

async function getImage(imgp) {
  var spath = fm.documentsDirectory() + imgp;
  var imgd;

  if (fm.fileExists(spath)) {
    var imgd = fm.readImage(spath);
  } else {
    var kit_logo_url =
      "http://www.great-research.eu/var/website/storage/images/media/images/partenaires/logo-du-kit/2557-1-eng-US/";
    var imgd = await new Request(kit_logo_url + imgp).loadImage();
    fm.writeImage(spath, imgd);
  }

  return imgd;
}

async function createWidget() {
  var kit_logo = await getImage("Logo-du-KIT_line_partner.jpg");
widget.addSpacer(5)
  logo_stack = widget.addStack();
  logo_stack.addImage(kit_logo);
  var data_url = "https://kit-bib-botv1.herokuapp.com/getplatz?username="+user
      
 var data = await new Request(data_url).loadJSON()
userdata = data

try{
    tstack = widget.addStack();
    tstack.centerAlignContent();
    var text = tstack.addText(userdata["when"]);
    text.font = new Font("arial", 12);
    text.centerAlignText();
    text.textColor = Color.black();
    widget.addSpacer(8)

// add headline
    rstack = widget.addStack();
    rstack.centerAlignContent();
    var text = rstack.addText(userdata["room"]);
    text.font = new Font("arial",20)
    text.centerAlignText();
    text.textColor = Color.black();


    // add headline
    tstack = widget.addStack();
    tstack.centerAlignContent();
    var text = tstack.addText(userdata["area_name"]);
    text.font = new Font("arial", 12);
    text.centerAlignText();
    text.textColor = Color.black();
    widget.addSpacer(8)
  

  
  }catch(error){ 
    console.log(error)
    // add headline
    rstack = widget.addStack();
    rstack.centerAlignContent();
    var text = rstack.addText("No data");
    text.font = new Font("arial",20)
    text.centerAlignText();
    text.textColor = Color.black();
    widget.addSpacer(10)
    
  }
   var currentdate = new Date()
   lastsync =  "Last Sync: " + currentdate.getDate() + "/"
                + (currentdate.getMonth()+1)  + "/" 
                + currentdate.getFullYear() + " @ "  
                + currentdate.getHours() + ":"  
                + currentdate.getMinutes() + ":" 
                + currentdate.getSeconds();
    
    // add headline
    rstack = widget.addStack();
    rstack.centerAlignContent();
    var text = rstack.addText(lastsync);
    text.font = new Font("arial",7)
    text.centerAlignText();
    text.textColor = Color.black();
    
  
}