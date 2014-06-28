function requisicao(acao, id, callback, erro)
{
  var url = '';
  if(acao == 'time') url = "retrieveInProgressSpectatorGameInfo/";
  else if(acao == 'league') url = "getLeagueForPlayer/";
  else if(acao == 'stats') url = "retrievePlayerStatsByAccountId/";
  else if(acao == 'nivel') url = "getSummonerByName/";
  else if(acao == 'champs') url = "retrieveTopPlayedChampions/";
  
  var server = $('#server').val();
  
  $.ajax({
    type: "GET",
    url: "https://community-league-of-legends.p.mashape.com/api/v1.0/"+server+"/summoner/"+url+"/"+id,
    headers: {"X-Mashape-Authorization" : "SsNckuwRAv3hFUeM6LHwrG8Ub3WEKXBP"}
  })
  .done(function( result ) {
    callback(result);
  })
  .error(function(){
    erro();
  });
}

var contaleague = 0;
var contaStats = 0;

function ordenarPlayers()
{
    if(contaleague == 10 && contaStats == 10)
    {
        $('.summoner').tsort({sortFunction:function(a,b){
            var order = ["CHALLENGER", "DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", ""];
            
            var valorA = a.e.find('.league').attr('title');
            var valorB = b.e.find('.league').attr('title');               
            
            if(valorA == valorB) 
            {
                var divA = a.e.find('.league span').attr('title');
                var divB = b.e.find('.league span').attr('title');
                
                if(divA == divB)
                {
                    var vitA = a.e.find('.pvp .victories').text();
                    var vitB = b.e.find('.pvp .victories').text();
                    
                    return parseInt(vitA) - parseInt(vitB) < 0;
                }
                
                return parseInt(divA) - parseInt(divB) < 0;
            }
            
            return order.indexOf(valorA) - order.indexOf(valorB) > 0;
        }});
    }
    else window.setTimeout(function(){ordenarPlayers();}, 1000);
}

function salvarCache()
{
  localStorage.setItem('TimeUm', $('#timeUm').html());
  localStorage.setItem('TimeDois', $('#timeDois').html());
  localStorage.setItem('Invocator', $('#nome').val());
  localStorage.setItem('Server', $('#server').val());
}

function translate(string)
{
    switch(string)
    {
        case 'Unranked': return 'PvP';
        case 'AramUnranked5x5': return 'ARAM';
        case 'RankedSolo5x5': return 'Ranked';
        return string;
    }
}

function getChamp(players, nome)
{
    for(var i in players)
    {
        if(players[i].summonerInternalName == nome)
            return {'id': players[i].championId, 'skin': players[i].selectedSkinIndex};
    }
    
}

function tratarNome(novoElem, summonerName)
{
    requisicao('nivel',+summonerName, function(data){
            if(data != null) novoElem.find('h1').attr('title', 'Nível '+data.summonerLevel+'');
        });
}

function tratarleague(novoElem, summonerId)
{
    requisicao('league', summonerId, function(data){
            if(data.error != null) novoElem.prepend('<div class="league" title=""><span title="0"></span></div>');                
            else 
            {
                switch(data.requestorsRank){case 'I':numero=1;break;case 'II':numero=2;break;case 'III':numero=3;break;case 'IV':numero=4;break;case 'V':numero=5;break;}
                novoElem.prepend('<div class="league '+data.tier+'" title="'+data.tier+'"><span title="'+numero+'">'+data.requestorsRank+'</span></div>');
            }
            contaleague++;
        });
}

function tratarStats(novoElem, accountId)
{
    requisicao('stats', accountId, function(data){
            stats = data.playerStatSummaries.playerStatSummarySet.array;
            var st = {};
            for(var i in stats)
            {
                var partida = translate(stats[i].playerStatSummaryTypeString);
                
                if(partida == 'ARAM' || partida == 'PvP' || partida == 'Ranked' )
                {
                    st[partida] = {};
                    st[partida]['victories'] = stats[i].wins;
                    st[partida]['derrotas'] = stats[i].losses;                      
                }
            }
    
    var maior = 0;
    if(st.PvP.victories > st.Ranked.victories && 
       st.PvP.victories > st.ARAM.victories) 
        maior = 1;
    if(st.Ranked.victories > st.PvP.victories && 
       st.Ranked.victories > st.ARAM.victories) 
        maior = 2;
    if(st.ARAM.victories > st.Ranked.victories && 
       st.ARAM.victories > st.PvP.victories) 
        maior = 3;
            
    string = '<li class="pvp '+(maior==1 ? 'grande' : '')+'"><strong>PvP</strong><span class="victories">'+st.PvP.victories+'</span><span class="derrotas">'+st.PvP.derrotas+'</span></li>';
    
            if(st.Ranked != null) 
        string += '<li class="ranked '+(maior==2 ? 'grande' : '')+'"><strong>Ranked</strong><span class="victories">'+st.Ranked.victories+'</span><span class="derrotas">'+st.Ranked.derrotas+'</span></li>';
    
            if(st.ARAM != null) 
        string += '<li class="aram '+(maior==3 ? 'grande' : '')+'"><strong>ARAM</strong><span class="victories">'+st.ARAM.victories+'</span><span class="derrotas">'+st.ARAM.derrotas+'</span></li>';
            
            novoElem.find('.vit').append(string);
            contaStats++;
        });
}

function tratarChamps(novoElem, accountId, champAtual)
{
    requisicao('champs', accountId, function(data){
        var array = data;

    var campeao = [];
    
    for(var i in array)
    {      
      champid = array[i].championId;
      stat = array[i].stats.array;
      
      campeao[champid] = {};
      campeao[champid].campeao = champid;      
      
      for(var x in stat)
      {
        var s = stat[x].statType;
        campeao[champid][s] = stat[x].value;
      }
      
    }
    
    campeao.sort(function(a, b){
      return b.TOTAL_SESSIONS_PLAYED - a.TOTAL_SESSIONS_PLAYED;
    });
    
    var string = '';
    for(var i in campeao)
    {
        string += '<li title="Kills: '+campeao[i].MAX_CHAMPIONS_KILLED+' Deaths: '+campeao[i].MAX_NUM_DEATHS+'"><img src="http://lkimg.zamimg.com/shared/riot/images/champions/'+campeao[i].campeao+'_32.png"><span class="percent">'+Math.floor((campeao[i].MAX_CHAMPIONS_KILLED / campeao[i].MAX_NUM_DEATHS)*100)+'%</span></li>';
    }   
            
            novoElem.find('.champs').append(string);
    
      for(var i in campeao) 
        if(campeao[i].campeao == champAtual)
        {
          novoElem.find('.champ .percent').text(Math.floor((campeao[i].MAX_CHAMPIONS_KILLED / campeao[i].MAX_NUM_DEATHS)*100)+'%').attr('title', 'Kills: '+campeao[i].MAX_CHAMPIONS_KILLED+' Deaths: '+campeao[i].MAX_NUM_DEATHS);
          break;
        }
        });
}

function tratarPlayer(idElem, jogador, selecao)
{
    var champ = getChamp(selecao, jogador.summonerInternalName);
    var string = '<a class="summoner" href="http://www.lolking.net/summoner/br/'+jogador.summonerId+'" target="_blank">'
                + '<div class="champ">'
        + '<span class="percent"></span>'
        + '<img src = "http://lkimg.zamimg.com/shared/riot/images/champions/'+champ.id+'_32.png"/></div>'
                + '<h3>'+jogador.summonerName+'</h3>'   
                + '<ul class="vit" title="Wins"></ul>'
        + '<br clear="all"/>'
        + '<ul class="champs" title="Most played"></ul>'
                + '</a>';
    novoElem = $(string).appendTo(idElem);
    
    //tratarNome(novoElem, jogador.summonerName);
    tratarleague(novoElem, jogador.summonerId);
    tratarStats(novoElem, jogador.accountId);
  tratarChamps(novoElem, jogador.accountId, champ.id);
}

function tratarTime(game)
{
    var time1 = game.teamOne.array;
    var time2 = game.teamTwo.array;
    var selecao = game.playerChampionSelections.array;
  
  $('#timeUm').html('<h2>'+game.gameType+'</h2>'); 
    
    for(var i in time1){tratarPlayer('#timeUm', time1[i], selecao);}
    for(var i in time2){tratarPlayer('#timeDois', time2[i], selecao);}
    
    ordenarPlayers();
  
  window.setTimeout(function(){
    contaleague = 10; 
    contaStats = 10;
    salvarCache();
  }, 20000)
}

function tratarSingle(nick)
{
    requisicao('nivel', nick, function(data){
        var string = '<a class="summoner" href="http://www.lolking.net/summoner/br/'+data.summonerId+'" target="_blank">'
                    + '<div class="champ">'
            + '<span class="percent"></span>'
            + '<img src = "http://lkimg.zamimg.com/shared/riot/images/profile_icons/profileIcon'+data.profileIconId+'.jpg" width="32" height="32"/></div>'
                    + '<h3>'+data.name+'</h3>'  
                    + '<ul class="vit" title="Wins"></ul>'
            + '<h4>Most Played</h4>'
            + '<ul class="champs"></ul>'
                    + '</a>';
        novoElem = $(string).appendTo('#timeUm');
        
        tratarleague(novoElem, data.summonerId);
        tratarStats(novoElem, data.acctId);
    tratarChamps(novoElem, data.acctId, 0);
    });
}

function executar()
{
  $('#timeUm, #timeDois').html('');
  var nick = $('#nome').val();
  $('#timeUm').html('<h2>Searching <strong>'+nick+'\'s</strong> game, wait...</h2>'); 
  requisicao('time', nick, function(data){
    if(data.error != null)
    { 
      $('#timeUm').html('<h2>Not in game</h2>'); 
      document.title = 'Not in game'; 
      tratarSingle(nick);
    }
    else 
    { 
      tratarTime(data.game); 
      document.title = "<strong>"+nick+"'s</strong> Game"; 
    }
  }, function(xhr, type){
    $('#timeUm').html('<h2>An error has occurred!</h2>'); 
  });  
}

(function(){
  var test = localStorage.getItem('TimeUm');
  if(!test){}
  else
  {
    $('#timeUm').html(localStorage.getItem('TimeUm'));
    $('#timeDois').html(localStorage.getItem('TimeDois'));
    $('#nome').val(localStorage.getItem('Invocator')).select();
    $('#server').val(localStorage.getItem('Server'));
  }
})();

$('input').keypress(function(e) {
  if(e.which == 13)
  { 
    executar(); 
    $('button').focus();
  }
})
$('button').on('click', function(){
    console.log("execute");
  executar()
});
