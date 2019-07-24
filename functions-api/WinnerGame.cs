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
using System.Net;
using System.Linq;
using Microsoft.WindowsAzure.Storage.Table;
using Siliconvalve.SelfieAndSeek.Models;

namespace Siliconvalve.SelfieAndSeek
{
    public static class WinnerGame
    {
        [FunctionName("WinnerGame")]
        [StorageAccount("GAMEDATA_STORAGE")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = null)] HttpRequest req, 
            [Table("gameconfig","config","bit")] GameConfig configItem, 
            [Table("regourls")] CloudTable playerImgTable, 
            [Table("playlogs")] CloudTable gameLogTable,
            ILogger log)
        {
            log.LogInformation($"Current Active Tier: {configItem.activetier}");

            var winnerQuery = new TableQuery<PlayLog>().Where(
                TableQuery.CombineFilters(
                    TableQuery.GenerateFilterConditionForInt("gamelevel", QueryComparisons.Equal, configItem.activetier),
                    TableOperators.And,
                    TableQuery.GenerateFilterCondition("status", QueryComparisons.Equal, "matched_bitly")));

            var winnerQuerySegment = await gameLogTable.ExecuteQuerySegmentedAsync(winnerQuery, null);

            if(winnerQuerySegment != null && winnerQuerySegment.Count() > 0)
            {
                configItem.currentwinner = winnerQuerySegment.First().PartitionKey;        
                configItem.winnersubmission = winnerQuerySegment.First().submittedimage;
            }

            log.LogInformation($"Looking up image for player: {configItem.currentwinner}");

            var playerImageQuery = new TableQuery<PlayerImage>().Where(
                TableQuery.CombineFilters(
                    TableQuery.GenerateFilterCondition("PartitionKey", QueryComparisons.Equal, configItem.currentwinner),
                    TableOperators.And,
                    TableQuery.GenerateFilterConditionForBool("selected", QueryComparisons.Equal, true)));

            var playerImageQueryResult = await playerImgTable.ExecuteQuerySegmentedAsync(playerImageQuery, null);

            if(playerImageQueryResult != null && playerImageQueryResult.Count() > 0)
            {
                configItem.winnerimgurl = playerImageQueryResult.First().imgurl;
            }    

            return (ActionResult)new OkObjectResult(configItem);
        }
    }
}