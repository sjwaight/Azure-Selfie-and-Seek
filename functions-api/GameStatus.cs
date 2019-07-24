using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Extensions.Storage;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System.Linq;
using Microsoft.WindowsAzure.Storage.Table;
using Siliconvalve.SelfieAndSeek.Models;

namespace Siliconvalve.SelfieAndSeek
{
     public static class GameStatus
    {
        [FunctionName("GameStatus")]
        [StorageAccount("GAMEDATA_STORAGE")]
        public static IActionResult Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = null)] HttpRequest req, 
            [Table("gameconfig","config","bit")] GameConfig configItem,
            ILogger log)
        {
            log.LogInformation($"GameStatus: {configItem.gamestatus}");
            return (ActionResult)new OkObjectResult(configItem.gamestatus);
        }
    }
}
