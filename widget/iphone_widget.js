const fm = FileManager.local();

const widget = new ListWidget();
widget.backgroundColor = Color.white();
await createWidget();
var smallfont = new Font("r", 10);
Script.setWidget(widget);
Script.complete();

async function getImage(imgp) {
  var spath = fm.documentsDirectory() + imgp;
  var imgd;

  if (fm.fileExists(spath)) {
    console.log("from storage");
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
  var kit_logo = getImage("Logo-du-KIT_line_partner.jpg");
  logo_stack = widget.addStack();
  logo_stack.addImage(kit_logo);
}
