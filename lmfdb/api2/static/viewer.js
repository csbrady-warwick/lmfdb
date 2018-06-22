

function fetch(offset, chunk){

  //Fetch the json data for this page, using the url given and specified offset

  var XHR = new XMLHttpRequest();
  url = dataRoot + dataSource;

  newUrl = addGetParam(url, '_view_start', offset);
  newUrl = addGetParam(newUrl, '_max_count', chunk);
  XHR.open('GET', newUrl);
  XHR.setRequestHeader('Content-Type', 'text/plain');

  XHR.addEventListener('load', function(event) {
    //On success fill in page data
  	var data = JSON.parse(XHR.response);
    console.log(XHR.response);
    clearData();
    if(jQuery.isEmptyObject(data)){
      onLoadingFail();
    }else{
      console.log(data.data);
      if(data.data.view_next == -1) hasMoreRecords = false;
      fillPage(data);
      $( document ).trigger("dataPopulated");
    }
  });

  // Define what happens in case of error
  XHR.addEventListener('error', function(event) {
    onLoadingFail();
  });

  XHR.send('');
}

function addGetParam(url, name, value){

  newUrl = url;
  hasGet = (newUrl.indexOf('?') != -1);
  if(hasGet){
    newUrl = newUrl + '&'; 
  }else{
    newUrl = newUrl + '?'; 
  }
  newUrl = newUrl + name + '=' + value;
  return newUrl;
}

function onLoadingFail(){
/* Actions if load fails
    Print message, disable prev.next buttons
*/
  console.log("Failed to fetch page data");
  div = document.getElementById('dataDiv');
  div.innerHTML = "<span class='err_text'>Failed to fetch page data. URL may not be valid</span>";

  $("input[type='button'][id*=ED").each(function() {
      this.disabled = true;
      this.classList.add('disabledbutton');
  });
}

function fetchInitial(){
  //Fetch initial record set
  fetch(0, defaultChunkSize);
}

function clearData(){

  dataDiv = document.getElementById('dataDiv');
  dataDiv.innerHTML = '';
}

function fillPage(data){
/* Fill the data
  Update the start and end and counts, and create one block per record
*/
  recordList = data.data.records;
  console.log("Fetched "+recordList.length +" records");
  updateRecordInfo(data.data.view_start, data.data.view_start + data.data.view_count -1, data.data.record_count);

  dataDiv = document.getElementById('dataDiv');

  for(var i = 0; i < recordList.length; i++){
    var div = document.createElement('div');

    var titleSpan = document.createElement('div');
    titleSpan.innerHTML = 'Record ' + i;

    var str = JSON.stringify(recordList[i], null, 2);
    var objDiv = document.createElement('code');
    objDiv.innerHTML = str;

    div.appendChild(titleSpan);
    div.appendChild(objDiv);
    dataDiv.appendChild(div);
  }
  window.scrollTo(0,0);
}

function updateRecordInfo(start, end, tot){
/* Update the start, end , of fields */
  var span = document.getElementById('num');
  span.innerHTML = start + ' to ' + end;

  var span = document.getElementById('totnum');
  span.innerHTML = tot;

}

function fetchNext(){

  if(hasMoreRecords){
    offset = offset + defaultChunkSize
    fetch(offset, defaultChunkSize);
  }else{
    alert('No further records to fetch');
  }
}

function fetchPrev(){

  if(offset > 0){
    offset = min(0, offset - defaultChunkSize);
    fetch(offset, defaultChunkSize);
  }else{
    alert('No previous records to fetch');
  }
}
