/**
 * Loading screen and progress bar management.
 * Must be included after nprogress.js
 */

document.covered = true;
        
document.removeCover = function() {
    document.covered = false;
    document.body.className = "";
    document.getElementById("overlay").className = "overlay-uncovered";
};

NProgress.work = 0;
NProgress.totalWork = 0;
NProgress.working = false;

function completePageLoad(){
    try {
        NProgress.done();
        NProgress.working = false;
    } finally {
        if (document.covered){
            document.removeCover();
            document.covered = false;
        }  
    }
};
    
NProgress.begin = function(){
    // TODO add timeout
    if (NProgress.working){
        return;
    }
    NProgress.working = true;
    NProgress.work = 0;
    NProgress.start();
};

NProgress.register = function(work){
    NProgress.totalWork += work ? work : 1;
};

NProgress.move = function(p){
    if (NProgress.working){
        NProgress.inc(p); 
    }
};

NProgress.advance = function (job, work, dontInc){
    try {
        if (job){
            job();
        }
    } finally {
        NProgress.work += work;
        if (NProgress.work<NProgress.totalWork){
            if (!dontInc){
                NProgress.move(NProgress.work/NProgress.totalWork); 
            }
        } else {
            completePageLoad();
        }
    }
};
        
function startPageLoadProgress(){
    try {
        NProgress && NProgress.show && NProgress.begin();
    } finally {
        // In case something goes wrong, at least show the page
        setTimeout(function(){
            completePageLoad();
        }, 15000); 
    }
};