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
using Siliconvalve.SelfieAndSeek.Models;

namespace Siliconvalve.SelfieAndSeek
{
    public static class ActiveGame
    {
        [FunctionName("ActiveGame")]
        [StorageAccount("GAMEDATA_STORAGE")]
        public static IActionResult Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = null)] HttpRequest req, 
            [Table("gameconfig","config","bit")] GameConfig configItem,
            ILogger log)
        {
            return (ActionResult)new OkObjectResult(configItem);
        }
    }
}
