using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System.Net;
using System.Linq;
using Microsoft.WindowsAzure.Storage.Table;

namespace Siliconvalve.SelfieAndSeek.Models
{
    public class GameConfig : TableEntity
    {
        public string gamestatus {get;set;}
        public string bitimgurl { get;set;}
        public string activeevent {get;set;}
        public string bitclearurl {get;set;}
        public string currentbit {get;set;}
        public string currentwinner {get;set;}
        public string winnersubmission {get;set;}
        public string winnerimgurl {get;set;}
        public int activetier {get;set;}

        public GameConfig()
        {
            PartitionKey = "config";
            RowKey = "bit";
        }
    }

    public class PlayerImage : TableEntity
    {
        public string imgurl {get;set;}
        public bool selected {get;set;}
        public PlayerImage()
        {}
    }

    public class PlayLog : TableEntity
    {
        public string status {get;set;}
        public int gamelevel {get;set;}
        public string submittedimage {get;set;}
        public PlayLog()
        {}
    }
}